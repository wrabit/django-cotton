export default (side, transitionEnterStart, transitionEnterEnd, transitionLeaveStart, transitionLeaveEnd) => ({
    side: side,
    transitionEnterStart: transitionEnterStart,
    transitionEnterEnd: transitionEnterEnd,
    transitionLeaveStart: transitionLeaveStart,
    transitionLeaveEnd: transitionLeaveEnd,
    root: {
        ['x-show']() {
            return this.$data['show'];
        },
        ['@click.stop']() {
            return true;
        },
        ['x-cloak']() {
            return true;
        },
        ['x-transition:enter']() {
            return "transition ease-linear duration-150";
        },
        ['x-transition:enter-start']() {
            return this.transitionEnterStart;
        },
        ['x-transition:enter-end']() {
            return this.transitionEnterEnd;
        },
        ['x-transition:leave']() {
            return "transition ease-linear duration-150";
        },
        ['x-transition:leave-start']() {
            return this.transitionLeaveStart;
        },
        ['x-transition:leave-end']() {
            return this.transitionLeaveEnd;
        },
    },
})
