require([
		"dojo/parser",
        "dojo/_base/declare",
        "dijit/form/DateTextBox",
        "dijit/Calendar"
], function (parser, declare, DateTextBox, Calendar) {

    var MyCalendar = declare("SurveyCalendar", Calendar, {
        getClassForDate: function (date) {
            if (!(date.getDate() % 10)) { return "red"; } // apply special style to all days divisible by 10
            console.log('getClassForDate');
        }
    });

    declare("SurveyCalendar", DateTextBox, {
        popupClass: SurveyCalendar
    });
});
