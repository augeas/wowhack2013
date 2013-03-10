<?php

include 'vendor/autoload.php';

$m = new MongoQB\Builder(array(
     'dsn'   =>  'mongodb://wowhack.alexbilbie.com:27017/wowhack'
));

if (isset($_POST['person_gender']))
{
   $m->where('person', $_POST['person_name'])->set('gender', $_POST['person_name'])->updateAll('people');
}

if (isset($_POST['author_gender']))
{
    $m->where('_id', $_POST['doc_url'])->set('author_gender', $_POST['author_gender'])->update('sources');
}


$people_count = $m->where('gender', 'u')->count('people');
$author_count = $m->where(['author_gender' => ['$exists' => false]])->count('sources');

$mode = 'person';

$offset = $_GET['offset'];

if ($people_count > 0) {
    $person = $m->where('gender', 'u')->limit(1)->offset($offset)->get('people');
    $doc = $m->where('_id', $person[0]['doc'])->get('sources');

    $name = $person[0]['person'];
    $author_gender = (isset($doc[0]['author_gender'])) ? $doc[0]['author_gender'] : 'unknown';
} else {
    $mode = 'doc';
}

?>

<h3><?=$people_count?> people left to categorise</h3>
<h3><?=$author_count?> authors left to categorise</h3>

<form method="post">

    <?php if ($mode === 'person'): ?>
    <p>

        <label for="person_gender">Is <?=$name?> male or female?</label>
        <input type="hidden" value="<?=$name?>" name="person_name">
        <select name="person_gender" id="person_gender">
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="unknown">Unknown</option>
        </select>

    </p>
    <?php endif; ?>

    <p>
        <label for="author_gender">Is the article author male or female?</label>
        <input type="hidden" value="<?=$doc[0]['_id']?>" name="doc_url">
        <select name="author_gender" id="author_gender">
            <option value="unknown" <?=($author_gender === 'unknown')?'selected':''?>>Unknown</option>
            <option value="male" <?=($author_gender === 'male')?'selected':''?>>Male</option>
            <option value="female" <?=($author_gender === 'female')?'selected':''?>>Female</option>
        </select>
    </p>

    <input type="submit" value="Update" name="update" id="update">

</form>

<input type="text" value="<?=$doc[0]['_id']?>" name="doc_url_plain">

<iframe height="600px" width="100%" src="<?=$doc[0]['_id']?>"></iframe>