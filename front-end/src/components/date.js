export function convertUTCDateToLocaleDate ( date )
{
    // Parse the utc date string to extract the date components

    const parsedDate = new Date( date );
    if ( date.includes( " GMT" ) )
    {
        return parsedDate
    }

    // Extract individual components
    const year = parsedDate.getFullYear();
    const month = parsedDate.getMonth();
    const day = parsedDate.getDate();
    const hour = parsedDate.getHours();
    const minute = parsedDate.getMinutes();
    const second = parsedDate.getSeconds();

    // Construct a new date in UTC
    return new Date( Date.UTC( year, month, day, hour, minute, second ) );
}

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
    return convertUTCDateToLocaleDate( timestamp ).toLocaleDateString( 'en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    } )
}