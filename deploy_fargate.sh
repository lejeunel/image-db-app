#!/usr/bin/env sh

# install nvm and nodejs
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.32.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 16
node -e "console.log('Running Node.js ' + process.version)"

# install fargate-deploy script if it doesn't exist
npm list fg-deploy || npm i -g @monsantoit/fg-deploy@latest

# install and start docker
sudo yum install -y docker
sudo systemctl start docker

source ./.env
npm set //npm.platforms.engineering/:_authToken $NPM_TOKEN
fg-deploy -m fg-deploy-np.js
