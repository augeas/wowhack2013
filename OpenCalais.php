<?php
class OpenCalais
{
	private $api_url = 'http://api.opencalais.com/tag/rs/enrich';
	private $api_key = '';
	private $output_format = 'Application/JSON';
	private $content_type = 'text/html';
	private $document;
	private $returns = array();

	public function __construct($new_api_key = NULL)
	{
		$this->api_key = $new_api_key;
	}

	public function get_entities($document)
	{
		if(empty($document))
		{
			throw new Exception('You need to provide a body of text to process.');
		}
		else
		{
			$this->document = $document;
			$this->api_call();
			return $this->returns;
		}
	}

	private function api_call()
	{
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, $this->api_url);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($ch, CURLOPT_HEADER, 0);
		curl_setopt($ch, CURLOPT_POSTFIELDS, $this->document);
		curl_setopt($ch, CURLOPT_POST, 1);
		curl_setopt($ch, CURLOPT_HTTPHEADER,
				array(
					'x-calais-licenseID: ' . $this->api_key,
					'content-type: ' . $this->content_type,
					'outputformat: ' . $this->output_format
				)
		);
		try
		{
			$response = json_decode(curl_exec($ch));
			foreach($response as $object)
		    {
		    	if((isset($object->instances)) AND ($object->_typeGroup !== 'relations'))
		    	{
		    		$temp = array();
		    		$temp['entity_text'] = $object->name;
		    		$temp['instance_count'] = count($object->instances);
		    		$temp['relevance_score'] = $object->relevance;

		    		$this->returns['entities'][$object->_type][] = $temp;
		       	}
		       	if((isset($object->_typeGroup)) AND ($object->_typeGroup === 'topics'))
		       	{
		       		$temp = array();
		       		$temp['entity_text'] = $object->categoryName;
		       		$temp['relevance_score'] = $object->score;

		       		$this->returns['topics'][] = $temp;
		       	}
		    }
		}
		catch(Exception $e)
		{
			echo 'An error occured when returning data from Open Calais.';
		}
	}

	public function get_returns()
	{
		return $this->returns;
	}

	public function unset_returns()
	{
		$this->returns = array();
	}
}