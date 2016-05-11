app.controller 'DemoController', [
  '$scope'
  ($scope)->
    $scope.menuItems = [
      # {
      #   name: '系统管理'
      #   items: [
      #     {name: '用户管理', url: '/admin/manage/user', icon:'fa-user', category: 'user'}
      #   ]
      # }
      {
        name: '内容管理'
        items: [
          {name: '文章管理', url: '/admin/manage/content', icon:'fa-file-text-o', category: 'content'}
          {name: '类别管理', url: '/admin/manage/category', icon:'fa-clipboard', category: 'category'}
        ]
      }
    ]

    $scope.isActive = (category, items)->
      if items
        if not angular.isArray(items)
          items = [items]
        for item in items
          if item.category is category
            return true
      return false
  ]
