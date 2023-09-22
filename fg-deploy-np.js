const {execSync} = require('child_process')

const gitCommand = 'git rev-parse HEAD'
const gitCommitHash = execSync(gitCommand).toString().trim()

module.exports = {
    name: 'imdb',
    fargateParameters: {
        cpu: '256',
        memory: '0.5GB',
        instanceCount: 2,
        healthCheckPath: '/ping',
        taskRoleName: 'dev-role',
        environmentVars: {
            IS_FARGATE: true,
            FARGATE_ENV: 'np',
        },
    },
    timeoutInSeconds: 900,
    aws: {
        accountId: '472901640203',
        fargateStackName: 'SC-472901640203-pp-xvzwkk55aisnm',
        region: 'us-east-1',
    }
}
