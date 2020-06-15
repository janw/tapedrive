import Vue from "vue"
import dayjs from "dayjs";
import duration from 'dayjs/plugin/duration';
import localizedFormat from "dayjs/plugin/localizedFormat";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(duration);
dayjs.extend(localizedFormat);
dayjs.extend(relativeTime);


Vue.filter("localDateTime", function (input) {
    return dayjs(input).format("LLL")
})

Vue.filter("fromLocalDateTime", function (input) {
    return dayjs(input).format("LLL")
})

Vue.filter("millisToTimestamp", function (milliseconds) {
    return new Date(milliseconds).toISOString().substr(11, 12);
})

Vue.filter("fromNow", function (input) {
    return dayjs(input).fromNow()
})
