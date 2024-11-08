export function convert_date_to_UTC ( date )
{
    // Parse the deadline date string to extract the date components

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

export const formatDate = ( timestamp ) =>
{
    return convert_date_to_UTC( timestamp ).toLocaleDateString( 'en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    } )
}