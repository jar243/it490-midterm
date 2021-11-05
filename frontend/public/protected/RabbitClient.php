<?php

require_once(__DIR__ . '../../../vendor/autoload.php');

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class RabbitClient
{
    private $host;
    private $port;
    private $user;
    private $pass;

    function __construct(string $host, int $port, string $user, string $pass)
    {
        $this->host = $host;
        $this->port = $port;
        $this->user = $user;
        $this->pass = $pass;
    }

    private function open_connection()
    {
        return new AMQPStreamConnection($this->host, $this->port, $this->user, $this->pass);
    }

    private function publish(string $route, array $args): object
    {
        $RES_QUEUE = 'amq.rabbitmq.reply-to';

        $connection = $this->open_connection();
        $channel = $connection->channel();

        $response = 'NO_RESPONSE_YET';
        $channel->basic_consume(
            $RES_QUEUE,
            '',
            false,
            true,
            false,
            false,
            function (AMQPMessage $message) use (&$response) {
                $response = $message->body;
            },
        );

        $json_body = json_encode($args);

        $msg = new AMQPMessage(
            $json_body,
            ['reply_to' => $RES_QUEUE],
        );

        $channel->basic_publish($msg, '', $route);
        while ($response == 'NO_RESPONSE_YET') {
            $channel->wait();
        }

        $channel->close();
        $connection->close();

        return json_decode($response);
    }

    public function log(string $log_msg)
    {
        $connection = $this->open_connection();
        $channel = $connection->channel();

        $channel->exchange_declare('logs', 'fanout');
        $body = [
            'sender' => 'frontend-php',
            'time' => date('Y/m/d H:i:s'),
            'msg' => $log_msg,
        ];
        $json_body = json_encode($body);
        $msg = new AMQPMessage($json_body);
        $channel->basic_publish($msg, 'logs');

        $channel->close();
        $connection->close();
    }

    public function user_create(string $username, string $display_name, string $email, string $password)
    {
        return $this->publish(
            'db.user.create',
            [
                'username' => $username,
                'display_name' => $display_name,
                'email' => $email,
                'password' => $password
            ]
        );
    }

    public function user_get_public(string $username)
    {
        return $this->publish(
            'db.user.get.public',
            ['username' => $username]
        );
    }

    public function user_get_private(string $token)
    {
        return $this->publish(
            'db.user.get.private',
            ['token' => $token]
        );
    }

    public function user_update(string $token, string $display_name, string $bio)
    {
        return $this->publish(
            'db.user.update',
            [
                'token' => $token,
                'display_name' => $display_name,
                'bio' => $bio
            ]
        );
    }

    public function token_generate(string $username, string $password)
    {
        return $this->publish(
            'db.token.generate',
            ['username' => $username, 'password' => $password]
        );
    }

    public function token_get_user(string $token)
    {
        return $this->publish(
            'db.token.get-user',
            ['token' => $token]
        );
    }

    public function token_delete(string $token)
    {
        return $this->publish(
            'db.token.delete',
            ['token' => $token]
        );
    }
}
