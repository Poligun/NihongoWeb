angular.module("nihongo")
.controller('SignInController', ['$scope', '$location', '$accountService',

function($scope, $location, $accountService) {
    $scope.signInForm = {
        email    : undefined,
        password : undefined
    }

    $scope.$watch(function() {
        return $accountService.alreadySignedIn();
    }, function(newValue, oldValue) {
        if (newValue)
            $location.url('');
    });

    $scope.signIn = function() {
        if ($scope.signInForm.email === undefined) {
            $scope.signInForm.status = 'error';
            $scope.signInForm.message = 'Invalid email address.';
        }

        else if ($scope.signInForm.password === undefined || $scope.signInForm.password == '') {
            $scope.signInForm.status = 'error';
            $scope.signInForm.message = 'Please enter password.';
        }

        else {
            $scope.signInForm.status = $scope.signInForm.message = '';
            $accountService.signIn($scope.signInForm.email, $scope.signInForm.password)
            .done(function() {
                $scope.$apply();
            }).fail(function(failMessage) {
                $scope.signInForm.status = 'error';
                $scope.signInForm.message = failMessage;
                $scope.$apply();
            });
        }
    }
}]);
