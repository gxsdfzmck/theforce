app = angular.module 'myapp', [
  'ui.bootstrap'
  'ivh.treeview'
  # 'ui.tree'
  # 'angularjs-datetime-picker'
  # 'datatables'
  # 'ng.ueditor'
  ]

# 修改{{}}为{[{ }]}，避免与handlebars冲突
app.config [
  '$interpolateProvider'
  ($interpolateProvider)->
    $interpolateProvider.startSymbol '{[{'
    $interpolateProvider.endSymbol '}]}'
  ]

app.filter 'to_trusted', [
  '$sce'
  ($sce)->
    (text)->
      $sce.trustAsHtml(text)
  ]


app.controller 'MyController', [
  '$scope', '$http', '$uibModal'
  ($scope, $http, $uibModal)->
    $scope.isProcessing = false
    $scope.selections = []
    $scope.isResultCollapsed = true
    $http.get('/fs').then (response)->
      $scope.filesystem = response.data
    , error_handler

    modalInstance = null
    error_handler = (response)->
      alert '发生错误'
      console.log response
      if modalInstance
        modalInstance.close()

    $scope.check = ->
      modalInstance = $uibModal.open
        animation: true
        templateUrl: 'loading.html'
        backdrop: 'static'
        size: 'lg'
      $http.post('/check', {fs: $scope.selections.join(',')}).then (response)->
        $scope.results = response.data
        $scope.isResultCollapsed = false
        modalInstance.close()
      , error_handler

    $scope.fscb = (ivhNode, ivhIsSelected, ivhTree)->
      selections = []
      stack = []
      stack.push(ivhTree)

      while true
        if stack.length == 0
          break
        item = stack.pop()
        if item.selected and item['value']
          selections.push(item['value'])
        if item['children']
          for i in item['children']
            stack.push(i)
      $scope.selections = selections
  ]

