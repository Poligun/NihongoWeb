var nihongoApp = angular.module("nihongo");

nihongoApp.config(['$routeProvider', function($routeProvider) {
    var templateFormat = '/static/nihongo/templates/{}.html';

    $routeProvider
    .when('/signin', {
        templateUrl : templateFormat.format('sign-in'),
        controller  : 'SignInController'
    })
    .when('/search/:searchIndex', {
        templateUrl : templateFormat.format('word-list'),
        controller  : 'WordListController'
    })
    .when('/question/', {
        templateUrl : templateFormat.format(''),
        controller  : ''
    })
    .otherwise({
        redirectTo: '/'
    });
}]);
