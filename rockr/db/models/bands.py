import rockr.db.rockr_db_manager as db


def get_bands():
    db_man = db.DbManager()
    cols = ['band_name', 'genre', 'members']
    res = db_man.select("bands", cols)
    bands = [{cols[0]: r[0], 
              cols[1]: r[1],
              cols[2]: r[2]} for r in res]
    return bands
