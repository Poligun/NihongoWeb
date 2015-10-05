angular.module("nihongo")
.controller('DialogsController', ['$scope', '$rootScope', '$apiService', '$accountService',

function($scope, $rootScope, $apiService, $accountService) {
    $scope.dialogs = [];

    $apiService.registerOnSessionExpiredHandler(function() {
        $scope.showDialog('Session Expired', 'Your session has expired, please sign in again.', ['OK'], function() {
            $accountService.clearLocalAccountData();
            return true;
        });
        $scope.$apply();
    });

    removeDialogAtIndex = function(dialogIndex) {
        $scope.dialogs.splice(dialogIndex, 1);
    }

    $scope.showDialog = function(title, content, actions, handler) {
        $scope.dialogs.push({
            title   : title,
            content : content,
            actions : actions || ['DISMISS'],
            handler : handler || function() { return true; },
            locked  : false
        });
    }

    $rootScope.showDialog = $scope.showDialog;

    $scope.onActionClicked = function(dialogIndex, actionIndex, actionName) {
        var dialog = $scope.dialogs[dialogIndex];

        if (!dialog.locked && typeof(dialog.handler) == 'function') {
            var returned = dialog.handler(actionIndex, actionName);

            if (typeof(returned) == 'boolean' && returned)
                removeDialogAtIndex(dialogIndex);

            else if (typeof(returned) == 'object' && returned.hasOwnProperty('then')) {
                dialog.locked = true;
                returned.then(function() {
                    removeDialogAtIndex(dialogIndex);
                    $scope.$apply();
                }).done(function() {
                    dialog.locked = false;
                });
            }
        }
    };
}]);
