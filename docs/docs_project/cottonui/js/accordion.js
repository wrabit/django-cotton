export default (type, collapsible, disabled) => ({
    value: type == 'single' ? '' : [],
    type: type,
    disabled: disabled,
    collapsible: collapsible,
})
