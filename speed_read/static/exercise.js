(function (){

var app = angular.module('exercise', [])

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
                var isVisible = data['visible']

                if (true || isVisible) {
                    $scope.isActive = data['active']
                    $scope.content = data['content']
                    $scope.nextLink = data['next_link']
                    console.log($scope.nextLink);
                    if (true || isActive) {


                    }
                    else {
                    }
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


app.directive('passage', function($window){
    return{
        restrict: 'E',
        templateUrl: '/static/passage.html',
        controller: function($scope){
            $scope.started = false;
            $scope.start_passage = function(){
                console.log('started')
                $scope.started = true;
            }
            $scope.stop_passage = function(){
                $window.location.href = $scope.nextLink;
            }
        },
        controllerAs: 'passage'
    }
});

app.directive('comprehension', function(){
    return {
        restrict: 'E',
        template: '<p>comprehension directive</p><p>{{ content }}</p>',
        link: function(element, scope, attrs){
        },
    };
});

app.directive('results', function(){
    return {
        restrict: 'E',
        template: '<p>results directive</p>'
    };
});

})();