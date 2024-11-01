import { useAlertStore } from '@/stores/alert.js'

export async function fetchfunct ( url, options = { headers: {} } )
{
    if ( options.headers )
    {
        options.headers[ "Authentication-Token" ] = localStorage.getItem(
            "Authentication-Token" )
    }
    else
    {
        options[ "headers" ] = {
            "Authentication-Token": localStorage.getItem(
                "Authentication-Token" )
        }

    }

    if ( !options.headers[ "Accept" ] )
    {
        options.headers[ "Accept" ] = "application/json"
    }
    return fetch( url, options ).catch( () => "Failed to fetch. Network error occured." )
}

export async function checkerror ( response )
{
    if ( response.status )
    {
        let data = await response.json()
        useAlertStore().alertpush( data.response.errors.map( e => { return { msg: e, type: 'alert-danger' } } ) )
    }

    else
    {
        useAlertStore().alertpush( [ { msg: response, type: 'alert-danger' } ] )
    }
}

export async function checksuccess ( response )
{
    let data = await response.json()
    useAlertStore().alertpush( [ { msg: data, type: 'alert-success' } ] )

}