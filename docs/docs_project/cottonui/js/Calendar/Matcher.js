export default class Matcher {
    constructor(rule) {
        this.type = this.determineMatcherType(rule)
        this.rule = rule;
    }

    passes(date) {
        date = this.createDateWithoutTime(date)
        if (this.type == 'dates') {
            return this.rule.dates.some(element =>  date.getTime() == this.createDateWithoutTime(element).getTime());
        } else if (this.type == 'range') {
            if (this.rule.before != null && date.getTime() < this.createDateWithoutTime(this.rule.before).getTime()) {
                return true
            }
            if (this.rule.after != null && date.getTime() > this.createDateWithoutTime(this.rule.after).getTime()) {
                return true
            }

            return false
        } else if (this.type == 'dayOfWeek') {
            if (typeof this.rule.dayOfWeek == 'number') {
               return date.getDay() == this.rule.dayOfWeek
            }else{
                return this.rule.dayOfWeek.some(rule => rule == date.getDay())
            }
        }

        return false
    }

    determineMatcherType(rule) {
        if (rule.dates != undefined && Array.isArray(rule.dates)) {
            return "dates"
        } else if (rule.before != undefined || rule.after != undefined) {
            return "range"
        } else if (rule.dayOfWeek != undefined) {
            return "dayOfWeek"
        }
    }

    createDateWithoutTime(value) {
        let date = new Date(value)
        date.setHours(0,0,0,0);

        return date;
    }
}
