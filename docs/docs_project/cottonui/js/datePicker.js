import { format as dateFormat } from "date-fns";

export default (open, value, mode, format) => ({
    open: open,
    value: null,
    mode: mode,
    format: format,
    root: {
        ['@keydown.esc']() {
            return this.closePicker();
        },
        ['x-cloak']() {
            return true;
        },
    },
    trigger: {
        ['@click']() {
            return this.togglePicker();
        },
        ['@keyup.esc']() {
            return this.closePicker();
        },
        ['@keydown.space']() {
            return this.togglePicker();
        },
        [':class']() {
            return !this.value && "text-muted-foreground";
        },
    },
    calendar: {
        ['x-show']() {
            return this.open;
        },
        ['x-cloak']() {
            return true;
        },
        ['x-transition']() {
            return true;
        },
        ['@click.away']() {
            return this.closePicker();
        },
        ['x-anchor.bottom-start.offset.3']() {
            return this.$refs.datePickerInput;
        },
        ['x-trap']() {
            return this.open;
        },
    },
    init() {
        this.value = value
    },
    openPicker() {
        this.open = true
    },
    closePicker() {
        this.open = false
    },
    togglePicker() {
        this.open ? this.closePicker() : this.openPicker()
    },
    formatDate(date) {
        if (date == null) {
            return null;
        }
        return dateFormat(new Date(date), this.format)
    }
})
