Migration to Colima - XPayroll


Step 1: Uninstall Docker 
Stop the Razorpay VPN
Quit Docker Desktop:
Ensure Docker Desktop is not running. Right-click the Docker icon in the menu bar and select Quit Docker Desktop.
Uninstall Docker Desktop:
On macOS, go to Applications and drag Docker to the Trash.
Alternatively, you can use this command to remove Docker Desktop files and configurations:
bash
Copy code
sudo rm -rf /Applications/Docker.app
sudo rm -rf ~/.docker
sudo rm -rf /Library/Containers/com.docker.docker
sudo rm -rf /Library/Group\ Containers/group.com.docker
Or uninstall from Razorpay self service
Remove Docker CLI and Daemon Binaries:
If you have Docker CLI tools installed via Homebrew, remove them:
bash
Copy code
brew uninstall --cask docker


Clean up any remaining Docker binaries:
bash
Copy code
sudo rm -f /usr/local/bin/docker*
Step 2: Install Colima
2.1 Install Colima:
brew install colima
2.2 Create the colima setup file
You can execute this file whenever you
Create a file in your home directory - start_colima.sh
Paste colima start --vm-type vz --cpu 4 --memory 8 --mount-type virtiofs --disk 200
For intel systems: paste colima start --cpu 4 --memory 8 --disk 200 
Run the script sh start_colima.sh
Colima should automatically set up a virtual environment for running containers compatible with Docker commands.s
2.3 Install Docker CLI:
Install Docker CLI tools to interact with Colima containers:
bash
Copy code
brew install docker
brew install docker-compose
Step 3: Verify Colima is Running
Run docker ps to ensure that Docker CLI is interacting with Colima and not Docker Desktop. You should see Colima containers running in the Docker context.
With these steps, Docker Desktop is uninstalled, and you have a fresh setup with Colima ready to use. Colima will handle container virtualization, allowing you to use Docker CLI commands without needing Docker Desktop.
Step 4: Setup Xpayroll monolith 
- Add line "127.0.0.1 www.localopfin.com" , "127.0.0.1 app.localopfin.com", "127.0.0.1 test.localopfin.com" and "127.0.0.1 webapp.localopfin.com" in /etc/hosts file (use ‘sudo vim hosts’, if u u don’t have permission to write file)
Checkout and pull the latest changes from branch master branch
Do docker login to harbor.razorpay.com -
Go to harbor.razorpay.com and login via SSO. 
Note the username and password (cli secret) from profile.
Run the command - docker login harbor.razorpay.com and login using the credentials noted above
If you are facing issues related to setting credentials, it might be because you might have set the credential store to docker desktop in some config in your PC. You need to remove it. 
Look for the entry credstore:”desktop” in ~/.docker/config.json
Removed the “credsStore” key or Replace it with "credsStore": "osxkeychain". Note:
 if you remove the key then you need to enter password everytime. 
Setup nginx - 
brew install nginx
add this code in the servers section(path: /opt/homebrew/etc/nginx/nginx.conf). (Just paste the line below the any server block). For intel systems the config path might be (path: /usr/local/etc/nginx/nginx.conf) or you can locate the path using command(locate nginx.conf) on your terminal.
server {
  listen 80;
  server_name  www.localopfin.com;
  location / {
      proxy_pass http://127.0.0.1:3020;
      proxy_set_header Host            $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      add_header       X-Upstream      $upstream_addr;
  }
}

server {
  listen 80;
  server_name  app.localopfin.com;
  location / {
      proxy_pass http://127.0.0.1:3020;
      proxy_set_header Host            $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      add_header       X-Upstream      $upstream_addr;
  }
}

server {
  listen 80;
  server_name  test.localopfin.com;
  location / {
      proxy_pass http://127.0.0.1:3020;
      proxy_set_header Host            $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      add_header       X-Upstream      $upstream_addr;
  }
}

server {
   listen 80;
   server_name webapp.localopfin.com;
   location / {
     proxy_pass http://127.0.0.1:3022;
     proxy_set_header Host      $host;
     proxy_set_header X-Forwarded-For $remote_addr;
     add_header    X-Upstream   $upstream_addr;
   }
 }

Run sudo nginx (or sudo nginx -s reload)
During the first time set-up, build/rebuild the image -> `sh docker-up.sh --build`. Your system will automatically ssh into the container. 
Run command ```sh entrypoint.sh load_php_libs``` 
Run command ```sh entrypoint.sh load_nodejs_libs``` 
Run command ```sh entrypoint.sh build_assets```
go to v2 folder. 	
To delete all existing rows in DB and run the fresh migration, run the command - `php artisan migrate:fresh`.
Create one user in the system by command. Run `php artisan tinker`. Run `App\Models\UserOrganization::factory()->create()`. Check the DB for the newly created user (there will be the xpayroll-system user, ignore that). You can now login with this user. Password is “password”
Populating local DB with users
Once your setup is complete, login as the user you created in Step 9	 above
Open this URL http://app.localopfin.com/v2/api/scenario/insurance/new 
If it runs correctly, you can check your DB and find it populated with dummy users and orgs
The most common error is it returning unauthorized. Log out and log in as that new user and it should work
Step 5: Add github token in ~/.zshrc
echo 'export GIT_USERNAME=<your github username>' >> ~/.zshrc 
echo 'export GIT_TOKEN=<your github token>' >> ~/.zshrc
source .zshrc
Step 6: Install payroll compute
Steps to run payroll compute service:
Go to the x-payroll-compute folder where you have cloned it from github
run make dev-docker-build
sh docker-up.sh
sh ssh-to-app.sh
Login to github
Run rm -f /tmp/git-askpass.sh && echo '#!/bin/sh' > /tmp/git-askpass.sh && echo 'echo "${GITHUB_TOKEN}"' >> /tmp/git-askpass.sh && chmod +x /tmp/git-askpass.sh && export GIT_ASKPASS=/tmp/git-askpass.sh
export GITHUB_TOKEN=<your github token>
make proto-generate-deps
make deps proto-refresh
go mod download && make go-build
run ./bin/api migrate up
Run Grpc server sh entrypoint.sh hotstart
Step 7: Install payroll salary structure
Steps to run payroll compute service:
Go to the x-salary-structure folder where you have cloned it from github
run make dev-docker-build
sh docker-up.sh
sh ssh-to-app.sh
go mod download && make go-build
run ./bin/api migrate up
Run Grpc server sh entrypoint.sh hotstart
Step 8: Test if you are able to run everything. Make sure you turn on rearch feature flag to test payroll compute and salary structure service. 
—--------------------------- Done Congratulations 🎉 —-----------------------------------------------
Few useful colima commands
Colima stop
Colima start
Colima ssh


Warning:
You will lose all your local data in the opfin DB. You can make backups and restore the volume of the DB if you want, google how to do that.

Terminate docker desktop
Install colima (https://github.com/abiosoft/colima)
run colima start --edit, it will open a config editor
set “vmType” as “vz”
set “mountType” as “virtiofs”
The above two is required to have your code changes reflect quickly in the container. Ref: Colima v0.5.0 increased my productivity | by Anthony Scata | Medium	
set memory to 4
Your docker image won’t run with the default 2gb setup. It would fail randomly
Save and close, colima will start
Build the docker image as usual and carry on


Tests:
Dashboard
Crons
Jobs, along with code changes reflecting in new jobs
Code changes reflecting in PHP in realtime
Unit tests
E2E
Logging 
React dev server with hot reload
—--------------------------------------------------------------------------

XPayroll services complete setup guide

Local setup for the devstack and devspace

brew install kubectl
kubectl
brew install helmfile
helmfile --version
brew install werf
werf version

Install DevSpace

curl -LO https://github.com/devspace-sh/devspace/releases/download/v5.18.5/devspace-darwin-arm64
chmod +x devspace-darwin-arm64
sudo mv devspace-darwin-arm64 /usr/local/bin/devspace


brew install int128/kubelogin/kubelogin


arch -arm64 sh -euo pipefail -c "$(curl 'https://get-devstack.dev.razorpay.in/')"
 


