export async function downloadFile ( response )
{
    // Extract filename from Content-Disposition header
    const contentDisposition = response.headers.get( 'Content-Disposition' );
    let filename = `${ new Date() }.pdf`; // default name

    if ( contentDisposition && contentDisposition.includes( 'filename=' ) )
    {
        // Extract filename from the header
        filename = contentDisposition
            .split( 'filename=' )[ 1 ]
            .replace( /['"]/g, '' ); // Remove any quotes
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL( blob );
    const link = document.createElement( 'a' );
    link.href = url;
    link.download = filename; // Use the extracted filename
    document.body.appendChild( link );
    link.click();
    link.remove();
    window.URL.revokeObjectURL( url );
};
