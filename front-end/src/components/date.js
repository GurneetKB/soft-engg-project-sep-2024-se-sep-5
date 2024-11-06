export function convert_date_to_UTC ( date )
{
    // Parse the deadline date string to extract the date components
    const parsedDate = new Date( date );

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
