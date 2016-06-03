def get_asset_content_by_id(asset, asset_content_id):
    for asset_content in asset.get_asset_contents():
        if str(asset_content_id) == str(asset_content.ident):
            return asset_content
    return None