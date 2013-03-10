<?php
use Guzzle\Http\Client;

require 'vendor/autoload.php';
require_once 'Readability.php';

$m = new MongoQB\Builder(array(
     'dsn'   =>  'mongodb://wowhack.alexbilbie.com:27017/wowhack'
));

$feeds = array(
    'http://www.pinknews.co.uk/feed/'   =>  'pinknews',
    'http://www.guardian.co.uk/rss' =>  'guardian',
    'http://www.timesonline.co.uk/tol/feeds/rss/topstories.xml' =>  'timesonline',
    'http://www.independent.co.uk/news/rss' =>  'independent',
    'http://feeds.bbci.co.uk/news/system/latest_published_content/rss.xml'  =>  'bbcnews',
    'http://www.scotsman.com/news'  =>  'scotsman',
    'http://www.ft.com/rss/home/uk' =>  'ft',
    'http://www.telegraph.co.uk/newsfeed/rss/news.xml'  =>  'telegraph',
    'http://www.dailymail.co.uk/pages/xml/index.html?in_page_id=1770'   =>  'dailymail',
    'http://dailyexpress.co.uk/rss/news.xml'    =>  'dailyexpress',
    'http://www.mirror.co.uk/news/latest/rss.xml'   =>  'mirror',
    'http://uk.dailystar.feedsportal.com/c/33335/f/565814/index.rss'    =>  'dailystar',
    'http://thesun.co.uk/sol/homepage/feeds/rss/article247682.ece'  =>  'thesun'
);

$sp = new SimplePie();


$stories = [];

foreach ($feeds as $feed => $name)
{
    echo 'Grabbing ' . $name . ' feed...';
    $sp->set_feed_url($feed);
    $sp->init();
    $sp->handle_content_type();

    foreach ($sp->get_items() as $item) {

        $stories[$item->get_permalink()] = $name;

    }

    echo 'grabbed' . PHP_EOL;

}

$i = 1;
foreach ($stories as $story => $source)
{
    $html = file_get_contents($story);
    $readability = new Readability($html, $story);
    $readability->debug = false;
    //$readability->convertLinksToFootnotes = true;
    $result = $readability->init();

    if ($result) {
        $content = $readability->getContent()->innerHTML;
        $content = strip_tags(str_replace(["\n", "\t"], [PHP_EOL, ''], $content));

        try {
            $m->insert('sources', [
                '_id'   =>  $story,
                'text'  =>  $content,
                'source'    =>  $source
            ]);
        } catch (Exception $e) {}

            echo $i . ') ' . $story . PHP_EOL;
            $i++;
    }
}