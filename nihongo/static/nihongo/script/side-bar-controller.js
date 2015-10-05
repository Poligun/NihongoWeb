angular.module("nihongo")
.controller('SideBarController', ['$scope', '$accountService',

function($scope, $accountService) {
    $scope.signOut = function() {
        $scope.showDialog(
            "Confirm Sign Out",
            "Local data will be dropped and you will be signed out.",
            ['CANCEL', 'CONFIRM'],
            function(index, action) {
                if (action == 'CONFIRM') {
                    return $accountService.signOut().done(function() {
                        $scope.showSideBar = false;
                        $scope.$apply();
                    });
                }
                else {
                    return true;
                }
            }
        );
    };
}]);
