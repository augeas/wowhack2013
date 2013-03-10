<?php

include 'vendor/autoload.php';
include 'OpenCalais.php';

$m = new MongoQB\Builder(array(
     'dsn'   =>  'mongodb://wowhack.alexbilbie.com:27017/wowhack'
));

$count = $m->count('sources');
$i = 0;
$people = 'foo';

while ($i < $count)
{
    $oc = new OpenCalais('yq54g9y5b5bx4j6g3kqc6mtp');
    $doc = $m->limit(1)->offset($i)->get('sources');
    $tags = $oc->get_entities($doc[0]['text']);
    $people = [];

    if (isset($tags['entities']['Person']))
    {

        foreach ($tags['entities']['Person'] as $person)
        {
            $people[] = $person['entity_text'];

            try {
                $m->insert('people', [
                    '_id'   =>  md5($doc[0]['_id'] . $person['entity_text']),
                    'doc'   =>  $doc[0]['_id'],
                    'person'    =>  $person['entity_text'],
                    'gender'    =>  'u',
                    'adjectives'    => []
                ]);
            } catch (Exception $e) {}
        }

        echo 'Found in ' . $doc[0]['_id'] . PHP_EOL . PHP_EOL . ' -> ' . implode(', ', $people) . PHP_EOL . PHP_EOL;
    }

    $people = [];
    $i++;
}