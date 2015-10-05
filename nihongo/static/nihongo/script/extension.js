String.prototype.format = function() {
    var newString = this;
    counter = 0;
    while (counter < arguments.length && newString.indexOf('{}') != -1) {
        newString = newString.replace('{}', arguments[counter++]);
    }
    matches = newString.match(/{[0-9]+}/g);
    if (matches != null) {
        for (var i = 0; i < matches.length; i++) {
            index = parseInt(matches[i].replace(/[{}]/g, ''));
            newString = newString.replace(matches[i], arguments[index]);
        }
    }
    return newString;
};
