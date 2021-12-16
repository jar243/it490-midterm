<?php

require_once(__DIR__ . '../../../vendor/autoload.php');

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;
use PhpAmqpLib\Exception\AMQPTimeoutException;

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

        try {
            $connection = $this->open_connection();
            $channel = $connection->channel();
        } catch (exception $e) {
            return (object) [
                'is_error' => true,
                'msg' => "Failed to connect"
            ];
        }

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
            try {
                $channel->wait(timeout: 5);
            } catch (AMQPTimeoutException $exc) {
                $channel->close();
                $connection->close();
                return (object) [
                    'is_error' => true,
                    'msg' => 'Request timed out'
                ];
            }
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

    public function friend_request_send(string $token, string $recipient_username)
    {
        return $this->publish(
            'db.friend-request.send',
            ['token' => $token, 'recipient_username' => $recipient_username]
        );
    }

    public function friend_request_accept(string $token, string $sender_username)
    {
        return $this->publish(
            'db.friend-request.accept',
            ['token' => $token, 'sender_username' => $sender_username]
        );
    }

    public function friend_request_decline(string $token, string $sender_username)
    {
        return $this->publish(
            'db.friend-request.decline',
            ['token' => $token, 'sender_username' => $sender_username]
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

    public function get_trending_movies()
    {
        return $this->publish(
            'api.trending.movies',
            ['placeholder' => '']
        );
    }

    public function get_popular_movies()
    {
        return $this->publish(
            'api.popular.movies',
            ['placeholder' => '']
        );
    }

    public function search_movies(string $search_query)
    {
        return $this->publish(
            'api.movies.search',
            ['query' => $search_query]
        );
    }

    public function get_movie(string $movie_id)
    {
        $db_res = $this->publish(
            'db.movie.get',
            ['movie_id' => $movie_id]
        );
        if ($db_res->is_error == true && $db_res->msg == "Movie must be added to database") {
            $api_res = $this->publish(
                'api.movies.get',
                ['movie_id' => $movie_id]
            );
            if ($api_res->is_error === false) {
                $add_res = $this->publish(
                    'db.movie.add',
                    (array) $api_res
                );
                if ($add_res->is_error === true) {
                    return $add_res;
                }
            }
            return $api_res;
        } else {
            return $db_res;
        }
    }

    public function submit_review(string $token, string $movie_id, int $stars, string $comment)
    {
        return $this->publish(
            'db.review.submit',
            [
                'token' => $token,
                'movie_id' => $movie_id,
                'stars' => $stars,
                'comment' => $comment
            ]
        );
    }

    public function get_watch_party(string $token, int $watch_party_id)
    {
        return $this->publish(
            'db.watch-party.get',
            [
                'token' => $token,
                'watch_party_id' => $watch_party_id
            ]
        );
    }

    public function schedule_watch_party(
        string $token,
        string $movie_id,
        int $movie_length,
        string $youtube_id,
        array $participants
    ) {
        return $this->publish(
            'db.watch-party.get',
            [
                'token' => $token,
                'movie_id' => $movie_id,
                'movie_length' => $movie_length,
                'youtube_id' => $youtube_id,
                'participants' => $participants
            ]
        );
    }

    public function leave_watch_party(string $token, int $watch_party_id)
    {
        return $this->publish(
            'db.watch-party.leave',
            [
                'token' => $token,
                'watch_party_id' => $watch_party_id
            ]
        );
    }

    public function play_watch_party(string $token, int $watch_party_id)
    {
        return $this->publish(
            'db.watch-party.play',
            [
                'token' => $token,
                'watch_party_id' => $watch_party_id
            ]
        );
    }

    public function pause_watch_party(string $token, int $watch_party_id)
    {
        return $this->publish(
            'db.watch-party.pause',
            [
                'token' => $token,
                'watch_party_id' => $watch_party_id
            ]
        );
    }
}
