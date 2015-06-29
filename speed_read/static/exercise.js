(function (){

var app = angular.module('exercise', ['ngCookies'])

app.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});


app.controller('passage', function($http, $scope, $element, $compile){
            $scope.started = (started == 'True')
            $scope.stopped = (stopped == 'True')
            $scope.startUrl = startUrl;
            $scope.stopUrl = stopUrl;

            $scope.start_passage = function(){
                console.log('started')
                $http.post($scope.startUrl).
                success(function(){
                    console.log('posted start');
                }).
            error(function(data, status, headers, config){
                console.log('failure')
                //this will eventually be taken out:
                var newElement = angular.element(data);
                newElement.insertAfter($element);
                $compile(newElement)($scope);
                })
            }
            $scope.stop_passage = function(){
                $http.post($scope.stopUrl).
                success(function(){
                    console.log('posted stop');
                })

            }
});

app.controller('comprehension', function($window, $scope, $http){



            //we have to wrap this functionality in a $watch so that
            //it gets run AFTER the asynchronous http request
            $scope.completedQuestions = 0;
            $scope.indices = [];

            $scope.$watch(function(){return $scope.content},
                          function(){
                            var i = 0;
                            for (var v in $scope.content) {
                                $scope.indices.push(i);
                                if ($scope.content[i].status != 2) {
                                    $scope.completedQuestions++;
                                }
                            i++;
                            }
                          });

            $scope.submitAnswer = function(question, correct) {

                console.log($scope.nextLink)
                    if (correct) {
                        question.status = 1;
                    } else {
                        question.status = 0;
                    }
                    $scope.completedQuestions++;
                    console.log('answered: ' + question + ' ' + correct);
                    }

            $scope.next = function(){
                $window.location.href = $scope.nextLink;
            }
        });

app.directive('question', function(){
    return {
        restrict: 'E',
        template: '<div>{{ id }}{{ text }}</div><div ng-transclude></div>',
        transclude: true,
        controller: function($scope, $element, $attrs){
            console.log('controller loaded');
            $scope.text = $attrs['text'];
            $scope.id = $attrs['id'];
            $scope.status = $attrs['status'];
            $scope.submit = function(question_id, correct){
                
            }
        }
    }
})

app.directive('choice', function(){
    return {
        scope: {},
        restrict: 'E',
        template: '<p><button></button></p>',
        controller: function($scope, $element, $attrs){
            console.log($scope.$parent.test);
        },
    }
});


app.directive('results', function(){
    return {
        restrict: 'E',
        templateUrl: '/static/results.html'
    };
});

})();