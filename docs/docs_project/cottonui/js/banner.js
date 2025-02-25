export default (displayAfter, transitionEnterStart, transitionEnterEnd, transitionLeaveStart, transitionLeaveEnd) => ({
    visible: false,
    displayAfter: displayAfter,
    transitionEnterStart: transitionEnterStart,
    transitionEnterEnd: transitionEnterEnd,
    transitionLeaveStart: transitionLeaveStart,
    transitionLeaveEnd: transitionLeaveEnd,
    root: {
        ['x-show']() {
            return this.visible;
        },
        ['x-cloak']() {
            return true;
        },
        ['x-transition:enter']() {
            return "transition ease-out duration-500";
        },
        ['x-transition:enter-start']() {
            return this.transitionEnterStart;
        },
        ['x-transition:enter-end']() {
            return this.transitionEnterEnd;
        },
        ['x-transition:leave']() {
            return "transition ease-in duration-300";
        },
        ['x-transition:leave-start']() {
            return this.transitionLeaveStart;
        },
        ['x-transition:leave-end']() {
            return this.transitionLeaveEnd;
        },
    },
    dismissTrigger: {
        ['@click']() {
            return this.dismiss();
        },
    },
    init() {
        setTimeout(() => { this.display() }, this.displayAfter);
    },
    display() {
        this.visible = true;
    },
    dismiss() {
        this.visible = false;
    }
})
