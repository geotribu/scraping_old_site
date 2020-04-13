#! python3  # noqa: E265

URLS_BASE_REPLACEMENTS = {
    # -- Custom images -- contributors
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/default_images/default-contributeur.png": "https://cdn.geotribu.fr/images/internal/charte/geotribu_logo_64x64.png",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/moi_cropped_0.jpg": "https://cdn.geotribu.fr/images/internal/contributeurs/mraj.jpg",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/profil_pro_jm.JPG": "https://cdn.geotribu.fr/images/internal/contributeurs/jmou.jpg",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/arnaud-vandecasteele_0_0.JPG": "https://cdn.geotribu.fr/images/internal/contributeurs/avdc.jpg",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/IMG_jeremie.JPG": "https://cdn.geotribu.fr/images/internal/contributeurs/jory.JPG",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/jeremie.jpg": "https://cdn.geotribu.fr/images/internal/contributeurs/jory.JPG",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/274955_528426175_572605730_n.jpg": "https://cdn.geotribu.fr/images/internal/contributeurs/avha.jpg",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/E.D.photo__0_0.jpg": "https://cdn.geotribu.fr/images/internal/contributeurs/edel.jpg",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeurs/photo_2011_1.png": "https://cdn.geotribu.fr/images/internal/contributeurs/tgra.jpg",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/styles/about_author/public/img/contributeursR.jpg": "https://cdn.geotribu.fr/images/internal/contributeurs/rbov.jpg",
    # -- Custom images -- Default news icon
    "http://localhost/sites/default/public/public_res/default_images/News.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_0.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_1.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_2.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_3.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_4.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_5.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_6.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/sites/default/public/public_res/default_images/News_7.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    # -- Custom images -- Default world icon
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/world.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/world_0.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/world_1.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/world_2.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/world_3.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/world_4.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/world_5.png": "https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
    # generic
    "http://localhost/sites/default/public/public_res/": "https://cdn.geotribu.fr/img/",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/img/": "https://cdn.geotribu.fr/img/",
    "http://localhost/geotribu_reborn/sites/default/public/public_res/default_images/": "https://cdn.geotribu.fr/img/",
    "http://geotribu.net/sites/default/public/public_res/img/": "https://cdn.geotribu.fr/img/",
    "http://www.geotribu.net/sites/default/public/public_res/img/": "https://cdn.geotribu.fr/img/",
}
