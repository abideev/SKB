#addin "Cake.Docker"
#addin "Cake.Http"
#addin nuget:?package=Newtonsoft.Json
#addin nuget:?package=Cake.DoInDirectory

var target = Argument("target", "Default");
var latestTag = Argument("latestTag", "latest");
var build_criterion = Argument("build_criterion", true);
var deploy_criterion = Argument("deploy_criterion", false);
var uninstall_criterion = Argument("uninstall_criterion", false);
var branch = Argument("branch", "");
var host = Argument("host", "");
var helmCommand = "upgrade --install --force";
var projectName = Argument("projectName", "");
var registryName = "custom-registry.example.com";
var DockerToken = Argument("token", "");
var UsernameRegistry = Argument("username", "default");

if(string.IsNullOrEmpty(DockerToken)) {
	throw new Exception("Could not get dockerToken");
}

Task("Build")
.WithCriteria(() => build_criterion)
.Does(() => {
    DoInDirectory("../sources/", () => {
       DockerBuild(new DockerImageBuildSettings {Tag  = new [] {$"{projectName}:latest"}}, "./");
    });
});


Task("Push-Image")
    .WithCriteria(() => build_criterion)
    .IsDependentOn("Build")
    .Does(() =>
{
    Information($"Tag image {projectName}:latest with {registryName}/{projectName}:{latestTag}");
    DockerLogin(new DockerRegistryLoginSettings{Password=$"{DockerToken}",Username=$"{UsernameRegistry}"});
    DockerTag($"{projectName}:latest", $"{registryName}/{projectName}:{latestTag}");
    DockerPush($"{registryName}/{projectName}:{latestTag}");
});


Task("Deploy")
    .WithCriteria(() => deploy_criterion)
    .IsDependentOn("Push-Image")
    .Does(()=>
{
        Information($"Deploy to k8s cluster:");
        DoInDirectory($"../ci-deploy/base", () => {
            var processArgumentBuilder = new ProcessArgumentBuilder();
            processArgumentBuilder.Append($"{helmCommand} {projectName}")
                                  .Append($"-f values.yaml")
                                  .Append($"-n {branch} --create-namespace")
                                  .Append($"--set image.tag={latestTag}")
                                  .Append($"--set image.repository={registryName}/{projectName}")
                                  .Append($"--set ingress.host={host}")
                                  .Append($"--set name={projectName}")
                                  .Append("--atomic --timeout 60s")
                                  .Append(".");

            var processSettingsRelease = new processSettingsRelease
            {
                Arguments = processArgumentBuilder
            };

            var exitCode = StartProcess("/usr/local/bin/helm", processSettingsRelease);
            if (exitCode != 0)
				Console.WriteLine ("Helm failed with exit code {0}", exitCode);
        });
});

Task("Uninstall")
    .WithCriteria(() => uninstall_criterion)
    .IsDependentOn("Deploy")
    .Does(()=>
    {
        Information($"Uninstall release: {projectName} in namespace {branch}");

        var processArgumentUninstaller = new processArgumentUninstaller();
            processArgumentUninstaller.Append($"{projectName}")
                                      .Append($"-n {branch}");
        var processSettingsUninstall = new processSettingsUninstall
        {
            Arguments = processArgumentUninstaller
        };

        var exitCode = StartProcess("/usr/local/bin/helm", processSettingsUninstall);
        if (exitCode != 0)
            Console.WriteLine ("Helm failed with exit code {0}", exitCode);
    });


Task("Default")
    .IsDependentOn("Uninstall");

RunTarget(target);
