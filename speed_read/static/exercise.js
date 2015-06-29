(function (){

var app = angular.module('exercise', ['ngCookies'])

app.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});


app.controller('exercise', function($http, $compile, $element, $scope){
            console.log('controller loaded.');
            // first get the url from the directive element to ask
            // about the server's status
            var statusUrl = $element[0].attributes['status-url'].value;
            var sectionType = $element[0].attributes['section'].value;

            $scope.isPassage = (sectionType === 'passage');
            $scope.isComprehension = (sectionType === 'comprehension');
            $scope.isResults =  (sectionType === 'results');


            $http.get(statusUrl).
            success(function(data, status, headers, config){
                console.log('success');
                $scope.isVisible = data['visible']

                if ($scope.isVisible) {
                    $scope.isActive = data['active']
                    $scope.content = data['content']
                    $scope.nextLink = data['next_link']
                } else {
                    console.log('invisible');
                    console.log('redirect to landing page?');
                }
            }).
            error(function(data, status, headers, config){
                console.log('failure')
                //this will eventually be taken out:
                var newElement = angular.element(data);
                newElement.insertAfter($element);
                $compile(newElement)(scope);
    })
});


app.directive('passage', function($window, $http){
    return{
        restrict: 'E',
        templateUrl: '/static/passage.html',
        controller: function($scope, $element){
            $scope.started = false;
            $scope.start_passage = function(){
                console.log('started')
                $scope.started = true;
                $http.post($scope.content.start_url).
                success(function(){
                    console.log('posted start');
                }).
            error(function(data, status, headers, config){
                console.log('failure')
                //this will eventually be taken out:
                var newElement = angular.element(data);
                newElement.insertAfter($element);
                $compile(newElement)(scope);
    })
            }
            $scope.stop_passage = function(){
                $http.post($scope.content.stop_url).
                success(function(){
                    console.log('posted stop');
                    $window.location.href = $scope.nextLink;
                })
            }
        },
        controllerAs: 'passage'
    }
});

app.directive('comprehension', function($window){
    return {
        restrict: 'E',
        templateUrl: '/static/comprehension.html',
        scope: false,
        controller: function($scope){



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
        },
    };
});


app.directive('results', function(){
    return {
        restrict: 'E',
        templateUrl: '/static/results.html'
    };
});

})();