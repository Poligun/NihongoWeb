angular.module("nihongo")
.controller('NaviBarController', ['$scope', '$location', '$wordService', '$historyService',

function($scope, $location, $wordService, $historyService) {
    var searchHistory = null;

    $scope.$on('$routeChangeSuccess', function(event, current, previous) {
        searchHistory = $historyService.getSearchHistory(current.params.searchIndex);
        $scope.searchInput = searchHistory.searchInput || '';
    });

    var uploadingRatio   = 0.1;
    var waitingRatio     = 0.7;
    var downloadingRatio = 1.0 - uploadingRatio - waitingRatio;
    var interval         = 1000 / 24;
    var timeLimit        = 8000;
    
    $scope.searchWord = function(searchInput) {
        if ($scope.searchLock)
            return;

        if ((searchInput = (searchInput || '').trim().replace(/[a-zA-Z0-9]+/g, '')) == '')
            return;

        var intervalId;

        clearProgress = function() {
            clearInterval(intervalId);
            $scope.searchLock = false;
            $scope.searchProgress = 0;
        }

        $scope.searchProgress = 0;

        $wordService.searchWord(searchInput)
        .progress(function(status, progress) {
            if (status == 'uploading')
                $scope.searchProgress = progress * uploadingRatio;

            else if (status == 'waiting') {
                var timeElapsed = 0;

                intervalId = setInterval(function() {
                    timeElapsed += interval;
                    if (timeElapsed >= timeLimit)
                        $scope.searchProgress = 0;
                    else
                        $scope.searchProgress = uploadingRatio + (timeElapsed / timeLimit) * waitingRatio;
                    $scope.$apply();
                }, interval);
            }

            else if (status == 'downloading')
                $scope.searchProgress = uploadingRatio + waitingRatio + progress * downloadingRatio;
        })

        .done(function(data) {
            clearProgress();
            
            var index = $historyService.addSearchHistory(searchInput, data.words);
            $location.url('search/{}'.format(index));
            $scope.$apply();
        })

        .fail(function(failMessage) {
            clearProgress();

            $scope.showDialog('Error occurred', failMessage, ['DISMISS'], function() { return true; });
            $scope.$apply();
        });

        $scope.searchLock = true;
    };
}]);
