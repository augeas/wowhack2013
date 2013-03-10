<?php

include 'vendor/autoload.php';
use Underscore\Types\Arrays;

$m = new MongoQB\Builder(array(
     'dsn'   =>  'mongodb://wowhack.alexbilbie.com:27017/wowhack'
));

$fh = fopen('adjectives.txt', 'r');
$allwords = fread($fh, filesize('adjectives.txt'));
fclose($fh);
$allwords = explode("\n", $allwords);

$count = $m->count('people');
$i = 0;

while ($i < $count)
{
	$person = $m->limit(1)->offset($i)->get('people');
	$doc = $m->where('_id', $person[0]['doc'])->get('sources');

	$name = $person[0]['person'];
	$nparts = explode(' ', $name);

	$text = explode('.', $doc[0]['text']);

	$found = [];

	foreach ($text as $sentance)
	{
		$sentance = trim($sentance);

		$sparts = explode(' ', $sentance);

		$nstart = null;
		$nend = null;

		$ii = 0;
		foreach ($sparts as $spart)
		{
			if ( ! is_null($nstart) && ! is_null($nend))
			{
				break;
			}

			if ($spart === $nparts[0])
			{
				$nstart = $ii;
				$nend = count($nparts) + $ii - 1;
			}

			$ii++;
		}

		if (is_null($nstart) && is_null($nend))
		{
			continue;
		}


		$before = ($nstart === 0) ? [] : @Arrays::first($sparts, $nstart);
		$after = @Arrays::last($sparts, count($nstart) - $nend - count($nparts));

		$before = @Arrays::first($before, 5);
		$after = @Arrays::last($after, 5);

		foreach ($before as $bword)
		{

			foreach ($allwords as $word)
			{
				similar_text($word, $bword, $p);
				if ($p >= 95)
				{
					$found[] = $word;
				}
			}

		}

		if (is_array($after))
		{
			foreach ($after as $aword)
			{

				foreach ($allwords as $word)
				{
					similar_text($word, $aword, $p);
					if ($p >= 95)
					{
						$found[] = $word;
					}
				}

			}
		}

	} // end each sentance

	$found = array_unique($found);

	if (count($found) > 0)
	{
		echo 'Tagging '.$name.' as: '.implode(',', $found).PHP_EOL;
	}



	$i++;

} // end each person