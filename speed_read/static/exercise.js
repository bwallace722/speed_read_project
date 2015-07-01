(function (){

var app = angular.module('exercise', ['ngCookies']);

app.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});

app.config(function ($httpProvider) {
  $httpProvider.defaults.transformRequest = function(data){
    if (data === undefined) {
      return data;
    }
    return $.param(data);
  };
  $httpProvider.defaults.headers.post['Content-Type'] = ''
    + 'application/x-www-form-urlencoded; charset=UTF-8';
});


app.controller('passage',
    function($http, $scope, $element, $compile, $window){
    $scope.started = (started == 'True')
    $scope.stopped = (stopped == 'True')
    $scope.startUrl = startUrl;
    $scope.stopUrl = stopUrl;
    $scope.nextUrl = nextUrl;

    $scope.start_passage = function(){
        console.log('started')
        $scope.started = true;
        $http({
            method: "POST",
            url: $scope.startUrl,
            data: {}}
            )
        .success(function(){
            console.log('posted start');
        })
        .error(function(data, status, headers, config){
            console.log('failure')
            //this will eventually be taken out:
            var newElement = angular.element(data);
            newElement.insertAfter($element);
            $compile(newElement)($scope);
        });
    }

    $scope.stop_passage = function(){
        $scope.stopped = true;
        $http({
            method: 'POST',
            url: $scope.stopUrl,
            data: {}})
        .success(function(){
            console.log('posted stop');
            console.log($scope.nextUrl)
            $window.location.href = $scope.nextUrl
            })
        }
});

app.controller('comprehension', function($element, $rootScope, $scope){
    $rootScope.question_list = [];
    $scope.$watch('$rootScope.question_list', function(){
        console.log('question_list changed');
        $rootScope.reveal_question();
    })
    //goes through all the buttons and reveals one if there's one to reveal
    $rootScope.reveal_question = function(){
        var revealed = false;
        for (q in $rootScope.question_list) {
            if (!revealed && !$rootScope.question_list[q].visible) {
                revealed = true;
                $rootScope.question_list[q].visible = true;
            }
        }
        if (!revealed) {
            console.log("show the next button");
            $scope.showNextLink = true;
        }
        console.log($rootScope.question_list);
    }
});

app.controller('question',
    function($rootScope, $scope, $element, $attrs, $http){
    $scope.question_id = $attrs['id'];
    $scope.status = $attrs['status'];
    $scope.visible = ($scope.status != '2');

    $scope.this_question = {'visible': $scope.status != '2'}

    $rootScope.question_list.push($scope.this_question)
    console.log($rootScope.question_list)

    $scope.submit = function(correct){
        console.log('submitted: ' + $scope.question_id + correct)
        $http({
            method: 'POST',
            url: statusLink,
            data: {'correct': correct,
                    'question_id': $scope.question_id}})
        .success(function(data){
            $scope.status = (correct = 'True' ? '1' : '0')
            console.log(data)
            $rootScope.reveal_question();
        })
        .error(function(data){
            //maybe not the call:
            //$rootScope.error = data;
            var newElement = angular.element(data);
            newElement.insertAfter($element);
        });
    }
});

app.controller('choice', function($scope, $element, $attrs){
    $scope.click = function(correct){
        $scope.submit($attrs['correct']);
    }
});

})();