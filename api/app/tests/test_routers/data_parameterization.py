data_params_test_register_valid_user = [
    # username, password, email

    # testing different passwords formats, same username. (all should return 200)

    # 8 characters password, no upper case letters, no special characters, no numbers
    ("Spotless9454", "wgteacgo"),

    # 8 characters password, numbers, upper case letters, no special characters
    ("Spotless9454", "abcDe8r8"),

    # 8 characters password, numbers, upper case letters, special characters
    ("Spotless9454", "^ZSnH9!n"),

    # 128 characters password, no upper case letters, no special characters, no numbers
    ("Spotless9454", "umhpjfkpjwgxdyodgzdngpprdcqixzsgjztirrjamkyyxzkmqhbseppdqrokxcyrempezirhrfibawgzerbvxcrmjrzkputqcrwouorcwqwbenugyyryxejbuvlfslxz"),

    # 128 characters password, numbers, upper case letters, no special characters
    ("Spotless9454", "Ai7WPwQ73ml9cATOpbJeoh6cblUBQIkrtUGtxiZi11fikOtQYc17QhPyLEB2gac1Rb4Vz663ledHPuvgE6Gv8DHJzuDN1HbUkv8zdi78HVNOftOxXFavJio138uzX764"),

    # 128 characters password, numbers, upper case letters, special characters
    ("Spotless9454", "O@8dYs41UCK^xNBs^57bjMHEnm^cTan#fytaoCqsox%5VOfyM98XD8XAOOKu3gGFeG@xe#pKo5G#APdHWdPicJH5Vm6Gd2usM4ceyw84mnB4bJygS*FPj$iZ6HOskgFm"),
]
