def month = env.Months

echo "============================================================"
echo " Starting AWS Cost and Usage Comparison "
echo " Total Number Of Recent Months to Test :  " + env.Months +   " "
echo "============================================================"

pipeline {
    agent{
        label 'Expensive-Node || A-Very-Expensive-Node || Another-Expensive-Nodel'
    }
   stages {
      stage('Prepare') {
         steps {
            checkout([$class: 'GitSCM', branches: [[name: '*/aws-services-boto3-python']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [credentialsId: 'sathish-anand', url: 'ssh://git@github.com:Sathish-Anand/aws-services-boto3-python.git']])
            sh label: '', script: 'sh aws-cost-and-usage/test/versionCheck.sh'
         }
      }
      stage('Build'){
          steps{
              git branch: 'aws-services-boto3-python', credentialsId: 'sathish-anand', url: 'ssh://git@github.com:Sathish-Anand/aws-services-boto3-python.git'
              sh label: '', script: "python3 aws-cost-and-usage/test/main.py --months='${env.months}'"
          }
      }
      stage('Test'){
          steps{
              echo 'Test Job'
          }
      }
   }

   post{
       success {
           notifyBuild('SUCCESSFUL')
           archiveArtifacts '*.csv'
       }
       failure{
           notifyBuild('FAILED')
           archiveArtifacts '*.csv'
       }
       }
}

def notifyBuild(String buildStatus = 'STARTED') {
  // build status of null means successful
  buildStatus =  buildStatus ?: 'SUCCESSFUL'

  // Default values
  def colorName = 'RED'
  def colorCode = '#FF0000'
  def customFailed = "AWS Cost Comparison Is Failed \n"
  def customSuccess = "AWS Cost Comparison Is Successful :) \n"
  def subject = "${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
  def summary = ""
  def details = """<p>STARTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
    <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>"""

  // Override default values based on build status
  if (buildStatus == 'STARTED') {
    color = 'YELLOW'
    colorCode = '#FFFF00'
  } else if (buildStatus == 'SUCCESSFUL') {
    color = 'GREEN'
    colorCode = '#00FF00'
    customSuccess = "AWS Cost Comparison Is Successful :) \n"
    summary = "${customSuccess} ${subject} (${env.BUILD_URL})"
  } else {
    color = 'RED'
    colorCode = '#FF0000'
    customFailed = "BUMMER!. AWS Cost Comparison Test Is Failed. :( \n"
    summary = "${customFailed} ${subject} (${env.BUILD_URL})"
  }
  // Send notifications
  slackSend (channel: 'sathish-tests', color: colorCode, message: summary, token: '***********')

}
