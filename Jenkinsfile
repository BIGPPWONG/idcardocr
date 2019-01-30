pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile'
    }

  }
  stages {
    stage('1') {
      steps {
        sh 'docker build -t test:0.1 .'
      }
    }
  }
}