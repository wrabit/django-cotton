export default class RangeModeHandler {
    constructor(required, min, max) {
        this.min = min
        this.max = max
        this.required = !!required;
    }

    dayClicked(date) {
        if (this._value.from == null || (this._value.to != null && this._value.to.getTime() == date.getTime())) {
            this._value.from = date
            this._value.to = null
            return true;
        }

        if (this._value.from.getTime() == date.getTime()) {
            this._value.from = this.required ? this._value.from : null
            this._value.to = null
            return true;
        }

        if (this._value.from.getTime() >= date.getTime()) {
            this._value.from = date
            return true;
        }

        this._value.to = date
        return true;
    }

    isSelectedDay(date) {
        if (this._value.from == null) {
            return false;
        }

        if (this._value.to == null) {
            return this._value.from.getTime() == date.getTime()
        }

        return date.getTime() == this._value.from.getTime() || date.getTime() == this._value.to.getTime()
    }

    get value() {
        return this._value
    }

    set value(value) {
        if (this._value == null) {
            this._value = { from: null, to: null };
        }

        if (value == null) {
            return;
        }

        const processDate = (input) => {
            if (input == null) return null;
            if (typeof input === "string") return this.createDateWithoutTime(input);
            if (input instanceof Date) return input;
            console.warn("Item is not a date or date string, skipping");
            return null;
        };

        this._value.from = processDate(value.from);
        this._value.to = processDate(value.to);
    }

    isDisabled(date) {
        if (this._value.from) {
            let daysBetween = Math.abs(this.getNumberOfDaysBetweenDates(this._value.from, date))
            return (((this.min && daysBetween < this.min) || (this.max && daysBetween > this.max)) && daysBetween != 0)
        }
    }

    isRangeMiddle(date) {
        if (this._value.from && this._value.to && date.getTime() >= this._value.from.getTime() && date.getTime() <= this._value.to.getTime()) {
            return true
        }

        return false
    }

    createDateWithoutTime(value) {
        let date = new Date(value)
        date.setHours(0, 0, 0, 0);

        return date;
    }

    getNumberOfDaysBetweenDates(date1, date2) {
        return Math.round((date1.getTime() - date2.getTime()) / (1000 * 3600 * 24));
    }
}
