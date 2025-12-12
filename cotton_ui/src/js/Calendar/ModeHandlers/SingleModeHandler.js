export default class SingleModeHandler {
    constructor(required) {
        this.required = !!required;
    }

    get value() {
        return this._value
    }

    set value(value) {
        const processDate = (input) => {
            if (input == null) return null;
            if (typeof input === "string") return this.createDateWithoutTime(input);
            if (input instanceof Date) return input;
            console.warn("Item is not a date or date string, skipping");
            return null;
        };
        this._value = processDate(value)
    }

    dayClicked(date) {
        if (this._value != null && this._value.getTime() == date.getTime() && !this.required) {
            this._value = null
        } else {
            this._value = date
        }
        return true
    }

    isSelectedDay(date) {
        return this._value?.getTime() === date.getTime();
    }

    isDisabled(date) {
        return false;
    }

    createDateWithoutTime(value) {
        let date = new Date(value)
        date.setHours(0, 0, 0, 0);

        return date;
    }
}
