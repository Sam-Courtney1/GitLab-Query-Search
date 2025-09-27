pipeline {
  agent { 
    node { 
      label 'small' 
    } 
  }
  options {
    buildDiscarder logRotator(
      artifactDaysToKeepStr: '', 
      artifactNumToKeepStr: '', 
      daysToKeepStr: '', 
      numToKeepStr: '30'
    )
    ansiColor('xterm')
  }
  parameters {
    string (
      name: 'QUERY_TEXT',
      defaultValue: '',
      description: 'Enter GitLab Query Variables',
      trim: true
    )
  }
  stages {
    stage('Set Build Description') {
      steps {
         script {
          currentBuild.description = "Query Text: ${params.QUERY_TEXT}"
        }
      }
    }
    stage('Install Dependencies') {
      steps {
        sh '''
            python3 -m ensurepip --upgrade
            pip3 install --upgrade --user setuptools
            pip3 install --user python-gitlab
            '''       
      }
    }
    stage('GitLab Query Search') {
      steps {
        withCredentials([
          sshUserPrivateKey(credentialsId: 'XYZ', keyFileVariable: 'KEY', usernameVariable: 'GIT_USER')
        ]) {
          script {
            wrap([$class: 'BuildUser']) {
                echo "Query being searched: ${params.QUERY_TEXT}"
                echo "Build triggered by: ${BUILD_USER_ID}"
                sh "python3 -u findQuery.py --SEARCH_WORDS \"${params.QUERY_TEXT}\""

                if (params.QUERY_TEXT?.trim()) {
                }
                else { 
                error "Please enter a String or Query to search"
                }

            }
          }
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts allowEmptyArchive: true, artifacts: '**/*.json, **/*.txt'
    }
    cleanup {
      cleanWs(
        deleteDirs: true,
        externalDelete: '/bin/rm -rf %s'
      )
    }
  }
}