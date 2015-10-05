var nihongoApp = angular.module('nihongo', ['ngRoute', 'ngAnimate'])

.provider('$apiService', [function() {
    var apiUrl = '/api';
    var timeout = 8000;

    var sessionExpiredHandlers = [];

    var sendRequest = function(action, data) {
        var deferred = $.Deferred();

        data['action'] = action;
        if (localStorage.hasOwnProperty('sessionToken'))
            data['sessionToken'] = localStorage.sessionToken;

        $.ajax({
            type    : 'POST',
            url     : apiUrl,
            data    : { data: angular.toJson(data) },
            timeout : timeout,
            xhr     : function() {
                var xhr = new window.XMLHttpRequest();

                xhr.upload.addEventListener('progress', function(event) {
                    if (event.lengthComputable) {
                        if (event.loaded == event.total)
                            deferred.notify('waiting', 0);
                        else
                            deferred.notify('uploading', event.loaded / event.total);
                    }
                }, false);

                xhr.addEventListener('progress', function(event) {
                    if (event.lengthComputable) 
                        deferred.notify('downloading', event.loaded / event.total);
                });

                return xhr;
            }
        }).done(function(data) {
            data = JSON.parse(data);
            if (!data.success) {
                if (data.exception == 'SessionExpired') {
                    $.each(sessionExpiredHandlers, function(index, handler) {
                        handler();
                    });
                }
                deferred.reject(data.exception);
            }
            else {
                deferred.resolve(data);
            }
        }).fail(function(XMLHttpRequest, statusText, errorThrown) {
            deferred.reject(String(errorThrown || statusText));
        });

        return deferred.promise();
    };

    this.$get = [function() {
        return {
            registerOnSessionExpiredHandler: function(handler) {
                sessionExpiredHandlers.push(handler);
            },
            sendAPIRequest: function(action, data) {
                return sendRequest(action, data);
            }
        };
    }];
}])

.service('$accountService', ['$apiService', function($apiService) {
    clearLocalAccountData = function() {
        delete localStorage.name;
        delete localStorage.email;
        delete localStorage.sessionToken;
    }

    this.clearLocalAccountData = clearLocalAccountData;

    this.alreadySignedIn = function() {
        return localStorage.hasOwnProperty('sessionToken');
    };

    this.signIn = function(email, password) {
        return $apiService.sendAPIRequest('signIn', {
            email    : email,
            password : password
        }).then(function(data) {
            localStorage.name = data.name;
            localStorage.email = data.email;
            localStorage.sessionToken = data.sessionToken;
        });
    };

    this.signOut = function() {
        return $apiService.sendAPIRequest('signOut', {})
        .then(function(data) {
            clearLocalAccountData();
        });
    };
}])

.service('$wordService', ['$apiService', function($apiService) {
    this.searchWord = function(word) {
        return $apiService.sendAPIRequest('searchWord', { word: word });
    };

    this.addWord = function(word) {
        return $apiService.sendAPIRequest('addWord', { word: word });
    };
}])

.service('$historyService', [function() {
    this.addSearchHistory = function(searchInput, words) {
        if (!sessionStorage.hasOwnProperty('searchHistoryCount'))
            sessionStorage.searchHistoryCount = 0;
        sessionStorage['searchHistory{}'.format (sessionStorage.searchHistoryCount)] = angular.toJson({
            index       : sessionStorage.searchHistoryCount,
            searchInput : searchInput,
            words       : words
        });
        return sessionStorage.searchHistoryCount++;
    };

    this.modifySearchHistory = function(searchHistory) {
        sessionStorage['searchHistory{}'.format(searchHistory.index)] = angular.toJson(searchHistory);
    };

    this.getSearchHistory = function(index) {
        var key = 'searchHistory{}'.format(index);

        if (sessionStorage.hasOwnProperty(key))
            return JSON.parse(sessionStorage[key]);
        else
            return { searchInput: '', words: [] };
    };
}])
