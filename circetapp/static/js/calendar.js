/**
 * WEBSITE: https://themefisher.com
 * TWITTER: https://twitter.com/themefisher
 * FACEBOOK: https://www.facebook.com/themefisher
 * GITHUB: https://github.com/themefisher/
 */

/* ====== Index ======

1. CALENDAR JS

====== End ======*/

document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  var year = new Date().getFullYear();
  var month = new Date().getMonth() + 1;
  function n(n) {
    return n > 9 ? "" + n : "0" + n;
  }
  var month = n(month);

  var calendar = new FullCalendar.Calendar(calendarEl, {
    plugins: ["dayGrid"],
    defaultView: "dayGridMonth",

    eventRender: function (info) {
      var ntoday = moment().format("YYYYMMDD");
      var eventStart = moment(info.event.start).format("YYYYMMDD");
      info.el.setAttribute("title", info.event.extendedProps.description);
      info.el.setAttribute("data-toggle", "tooltip");
      if (eventStart < ntoday) {
        info.el.classList.add("fc-past-event");
      } else if (eventStart == ntoday) {
        info.el.classList.add("fc-current-event");
      } else {
        info.el.classList.add("fc-future-event");
      }
    },

    events: [
    
    ],
  });

  calendar.render();
});
