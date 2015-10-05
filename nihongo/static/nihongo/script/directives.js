var nihongoApp = angular.module("nihongo");
var templateUrlFormat = '/static/nihongo/templates/{}.html';

nihongoApp.directive('ngEnter', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.bind('keydown', function(event) {
                if (event.which == 13) {
                    scope.$apply(function() {
                        scope.$eval(attrs.ngEnter);
                    });
                    event.preventDefault();
                }
            });
        }
    };
});

nihongoApp.directive('icon', [function() {
    return {
        restrict: 'E',
        scope: {
            name: '@',
            classes: '@'
        },
        template: '<span class="material-icons {{classes}}">{{name}}</span>'
    }
}]);

nihongoApp.directive('navibar', [function() {
    return {
        restrict: 'E',
        controller: 'NaviBarController',
        templateUrl: templateUrlFormat.format('navi-bar')
    }
}]);

nihongoApp.directive('sidebar', [function() {
    return {
        restrict: 'E',
        controller: 'SideBarController',
        templateUrl: templateUrlFormat.format('side-bar')
    }
}]);

nihongoApp.directive('dialogs', [function() {
    return {
        restrict: 'E',
        controller: 'DialogsController',
        templateUrl: templateUrlFormat.format('dialogs')
    }
}]);

nihongoApp.directive('example', ['$compile', function($compile) {
    return {
        restrict: 'E',
        scope: {
            example: '='
        },
        link: function(scope, element, attrs) {
            var occurences = [];
            for (var i = 0; i < scope.example.occurences.length; i++) {
                occurences.push('<span class="occurence">{}</span>'.format(scope.example.occurences[i]));
            }
            var template = '<span>{}</span>'.format(scope.example.example.format.apply(scope.example.example, occurences));
            element.replaceWith($compile(template)(scope));
        }
    }
}]);

nihongoApp.directive('slideInOut', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var left = 0;
            var duration = 300;

            element.addClass('ng-hide');

            scope.$watch(attrs.slideInOut, function(newValue, oldValue) {
                if (newValue) {
                    element.css('left', left - element.width());
                    element.removeClass('ng-hide').animate({'left': left}, duration);
                } else if (!element.hasClass('ng-hide')) {
                    element.animate({'left': left - element.width()}, duration, function() {
                        element.addClass('ng-hide');
                    });
                }
            });
        }
    }
});

nihongoApp.directive('slideUpDown', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var duration = 300;
            var height;

            element.addClass('ng-hide');
            scope.$watch(attrs.slideUpDown, function(newValue, oldValue) {
                if (newValue) {
                    element.removeClass('ng-hide').animate({'height': height}, duration, function() {
                        element.removeAttr('style');
                    });
                } else if (!element.hasClass('ng-hide')) {
                    height = element.height();
                    element.animate({'height': 0}, duration, function() {
                        element.addClass('ng-hide');
                    });
                }
            });
        }
    }
});

nihongoApp.directive('progress', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            scope.$watch(attrs.progress, function(newValue, oldValue) {
                if (newValue === undefined || newValue >= 1.0) {
                    element.css('width', '0');
                } else {
                    if (newValue < 0.0) {
                        newValue = 0.0;
                    }
                    element.css('width', '{}%'.format(newValue * 100));
                }
            });
        }
    }
});
