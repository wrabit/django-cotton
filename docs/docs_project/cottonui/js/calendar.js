import Matcher from "./Calendar/Matcher"
import MultipleModeHandler from "./Calendar/ModeHandlers/MultipleModeHandler"
import RangeModeHandler from "./Calendar/ModeHandlers/RangeModeHandler"
import SingleModeHandler from "./Calendar/ModeHandlers/SingleModeHandler"

export default (selected, mode, disabled, min, max, required) => ({
    focusedDay: '',
    mode: mode,
    max: max,
    min: min,
    month: '',
    year: '',
    daysInMonth: [],
    preBlankDaysInMonth: [],
    postBlankDaysInMonth: [],
    modeHandler: null,
    disabled: [],
    monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    days: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    root: {
        ['@keydown.left.prevent']() {
            this.focusAdd(-1)
        },
        ['@keydown.right.prevent']() {
            this.focusAdd(1)
        },
        ['@keydown.up.prevent']() {
            this.focusAdd(-this.days.length)
        },
        ['@keydown.down.prevent']() {
            this.focusAdd(this.days.length)
        },
        ['x-transition']() {
            return true;
        },
    },
    previousMonthTrigger: {
        ['@click']() {
            this.previousMonth()
        },
    },
    nextMonthTrigger: {
        ['@click']() {
            this.nextMonth()
        }
    },
    yearLabel: {
        ['x-text']() {
            return this.year
        }
    },
    monthLabel: {
        ['x-text']() {
            return this.monthNames[this.month]
        }
    },
    init() {
        if (this.mode == "single") {
            this.modeHandler = new SingleModeHandler(required)
        } else if (this.mode == "multiple") {
            this.modeHandler = new MultipleModeHandler(required, min, max)
        } else if (this.mode == "range") {
            this.modeHandler = new RangeModeHandler(required, min, max)
        } else {
            console.error("Mode is invalid, defaulting to single mode")
            this.modeHandler = new SingleModeHandler(required)
        }

        // add items to the disabled rules array
        if (Array.isArray(disabled)) {
            disabled.forEach((element) => {
                this.disabled.push(new Matcher(element))
            });
        } else if (typeof disabled == 'object' && disabled != null) {
            this.disabled = [new Matcher(disabled)]
        }

        let now = new Date();
        this.month = now.getMonth();
        this.year = now.getFullYear();
        this.focusedDay = now.getDay();
        this.calculateDays();

        if (!!selected) {
            this.dispatchChange()
        }
    },
    dispatchChange() {
        this.$nextTick(() => { this.$dispatch('change', { value: this.modeHandler.value }) })
    },
    dayClicked(date) {
        let selectedDate = new Date(this.year, this.month, date);
        if (this.isDisabled(selectedDate)) {
            return;
        }
        this.focusedDay = date;
        let dispatchEvent = this.modeHandler.dayClicked(selectedDate)
        if (dispatchEvent) {
            this.dispatchChange()
        }
    },
    focusAdd(value) {
        if (!Number.isInteger(this.focusedDay)) {
            this.focusedDay = (new Date(this.year, this.month, day)).getDate();
        }
        this.focusedDay = this.focusedDay + value;
        if (this.focusedDay > this.daysInMonth.length) {
            this.focusedDay = this.focusedDay - this.daysInMonth.length;
            this.nextMonth();
        }
        else if (this.focusedDay <= 0) {
            this.previousMonth();
            this.focusedDay = this.daysInMonth.length + this.focusedDay
        }
    },
    previousMonth() {
        if (this.month == 0) {
            this.year--;
            this.month = 12;
        }
        this.month--;
        this.calculateDays();
    },
    nextMonth() {
        if (this.month == 11) {
            this.month = 0;
            this.year++;
        } else {
            this.month++;
        }
        this.calculateDays();
    },
    isSelectedDay(day) {
        let date = new Date(this.year, this.month, day)
        return this.modeHandler.isSelectedDay(date)
    },
    isFocusedDate(day) {
        return this.focusedDay === day ? true : false;
    },
    isToday(day) {
        const today = new Date();
        const d = new Date(this.year, this.month, day);
        return today.toDateString() === d.toDateString() ? true : false;
    },
    calculateDays() {
        let daysInMonth = new Date(this.year, this.month + 1, 0).getDate();
        let daysInPreviousMonth = new Date(this.year, this.month, 0).getDate();
        // find where to start day of week
        let dayOfWeek = new Date(this.year, this.month).getDay();
        let preBlankdaysArray = [];
        for (var i = 1; i <= dayOfWeek; i++) {
            preBlankdaysArray.push(daysInPreviousMonth - i + 1);
        }

        //if the length of the preblank arrays is a multiple of the week, it is considered an entire week
        preBlankdaysArray = preBlankdaysArray.reverse();
        let postBlankdaysArray = [];
        // always display 6 rows
        for (var i = 1; i <= (this.days.length * 6 - (preBlankdaysArray.length + daysInMonth)); i++) {
            postBlankdaysArray.push(i);
        }
        let daysArray = [];
        for (var i = 1; i <= daysInMonth; i++) {
            daysArray.push(i);
        }
        this.preBlankDaysInMonth = preBlankdaysArray;
        this.postBlankDaysInMonth = postBlankdaysArray;
        this.daysInMonth = daysArray;
    },
    isDisabled(date) {
        return this.disabled.some(rule => rule.passes(date)) || this.modeHandler.isDisabled(date);
    },
    isRangeMiddle(date) {
        if (mode == 'range') {
            return this.modeHandler.isRangeMiddle(date)
        }

        return false
    }
})
