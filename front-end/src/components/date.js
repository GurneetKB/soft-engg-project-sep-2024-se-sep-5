export const localDateInISOFormat = ( date ) =>
{
    return date.getFullYear() +
        "-" + String( date.getMonth() + 1 ).padStart( 2, '0' ) +
        "-" + String( date.getDate() ).padStart( 2, '0' ) +
        "T" + String( date.getHours() ).padStart( 2, '0' ) +
        ":" + String( date.getMinutes() ).padStart( 2, '0' )
}

export const formatDate = ( timestamp ) =>
{
    return new Date( timestamp ).toLocaleDateString( 'en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    } )
}