angular.module("nihongo")
.controller('NihongoController', ['$scope', '$location', '$accountService',

function($scope, $location, $accountService) {
    $scope.name = 'NihongoController';

    $scope.$watch(function() {
        return $accountService.alreadySignedIn();
    }, function(newValue, oldValue) {
        if (!newValue)
            $location.url('signin');
    });
}]);
