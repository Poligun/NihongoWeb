angular.module("nihongo")
.controller('WordListController', ['$scope', '$route', '$wordService', '$historyService',

function($scope, $route, $wordService, $historyService) {
    var searchHistory = null;

    $scope.$on('$routeChangeSuccess', function(event, current, previous) {
        searchHistory = $historyService.getSearchHistory(current.params.searchIndex);
        $scope.words = searchHistory.words || [];
    });

    $scope.addWord = function(word) {
        $scope.showDialog(
            'Add This Word To Dictionary?',
            '{}（{}） will be added, which can be modified later.'.format(word.word, word.kana),
            ['CANCEL', 'ADD'],
            function(index, action) {
                if (action == 'ADD') {
                    var deferred = $.Deferred();

                    $wordService.addWord(word)
                    .done(function(data) {
                        for (var i = 0; i < $scope.words.length; i++) {
                            if ($scope.words[i] === word) {
                                $scope.words[i] = data.word;
                                break;
                            }
                        }
                        searchHistory.words = $scope.words;
                        $historyService.modifySearchHistory(searchHistory);
                        deferred.resolve();
                    })

                    .fail(function(failMessage) {
                        $scope.showDialog('Failed To Add This Word', failMessage);
                        deferred.resolve();
                    });

                    return deferred.promise();
                }
                else {
                    return true;
                }
            }
        );
    }
}]);
