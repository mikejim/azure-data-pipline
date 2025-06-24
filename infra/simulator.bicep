resource containerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: 'netflix-simulator'
  location: resourceGroup().location
  properties: {
    kubeEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [{
        server: 'sparkacr001.azurecr.io'
        username: '<acr-username>'
        password: '<acr-password>'
      }]
    }
    template: {
      containers: [{
        name: 'simulator'
        image: 'sparkacr.azurecr.io/netflixsim:latest'
        resources: {
          cpu: 0.5
          memory: '1Gi'
        }
        env: [
          {
            name: 'EVENT_HUB_CONN_STR'
            value: '<your-event-hub-connection-string>'
          }
        ]
      }]
      scale: {
        minReplicas: 1
        maxReplicas: 2
        rules: []
      }
    }
  }
}
